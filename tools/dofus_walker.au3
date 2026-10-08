; ============================================================================
;  dofus_walker.au3 — Daemon auto-clic A -> B pour Dofus Retro (ile de Pandala)
; ----------------------------------------------------------------------------
;  N'ENVOIE RIEN AU SERVEUR. Clique la CELLULE DE SORTIE de la map. Le VRAI
;  client joue. Zero reseau.
;
;  MODE DAEMON : ne touche plus au script. Lance-le une fois et laisse-le
;  tourner. Le pilotage se fait DEPUIS live.html :
;    - clic sur un compte de la carte, puis clic sur la case destination,
;    - le walker recupere le job (/walk/job), marche, et rapporte l'avancement.
;
;  Chaine par pas :
;   1) /walk/job     -> job courant (compte + destination) pose par live.html
;   2) /live/state   -> position + map_id du perso pilote
;   3) /route/path   -> prochaine direction (BFS sur MAP_COORDS)
;   4) /map/exit     -> cellule de sortie (0-559) de cette map/direction
;   5) cellule->pixel-> transfo isometrique (mapWidth=15) + affine -> clic
;   6) /walk/status  -> rapporte l'etat (live.html l'affiche)
;
;  STOP : Echap.   Journal : tools\dofus_walker.log
; ============================================================================

#include-once
#include <Misc.au3>
DllCall("user32.dll", "int", "SetProcessDPIAware")
; Desactive le VERROU DE 1er PLAN de Windows (SPI_SETFOREGROUNDLOCKTIMEOUT=0x2001).
; Sans ca, un process en arriere-plan (ce walker) ne peut pas forcer WinActivate
; quand une autre fenetre (le navigateur) est au 1er plan -> le clic "activer la
; fenetre" du board/carte ne faisait que clignoter la barre des taches.
DllCall("user32.dll", "bool", "SystemParametersInfoW", "uint", 0x2001, "uint", 0, "ptr", 0, "uint", 0)
Opt("MouseCoordMode", 1)
Opt("TrayIconDebug", 1)
Opt("WinTitleMatchMode", 2)   ; 2 = titre en sous-chaine (le titre = "Styxh-[Gal] - Dofus Retro v1.49.5")

; une seule instance (le bouton "Lancer" de live.html ne doit pas en ouvrir 2)
If Not _Singleton("dofus_walker_daemon", 1) Then Exit

; ======================= CONFIG ============================================ ;
Global $g_sApi = "http://localhost:8000"
; True = active la fenetre du client (par NOM DE PERSO, present dans le titre)
; avant chaque clic -> plus besoin d'alt-tab, et vise le bon client en multi-compte.
Global $g_bActivateWin = True

; --- Transformation cellule -> pixel ecran (calee sur 5 relevés, residu ~1px)
Global Const $MAP_WIDTH = 15
; ecranX = CX0*gx + CX1*gy + CX2 ; ecranY = CY0*gx + CY1*gy + CY2
Global $g_aCX[3] = [67.9685, -68.0861, 845.5]
Global $g_aCY[3] = [34.2476, 34.6212, 30.6]

Global $g_iPollMs       = 1000
Global $g_iIdlePollMs   = 1500
Global $g_iChangeToMs   = 45000   ; absorbe le retard sniffer (~25s)
Global $g_iAfterClickMs = 800
Global $g_iStepWalkMs   = 1600   ; donjon : attente entre 2 cases d'une meme salle
;                                 (le temps que le perso marche jusqu'a la case)
Global $g_iWinReportMs  = 3000   ; board : frequence de report des fenetres Dofus
Global $g_iLastWinReport = 0
; ordre STABLE des fenetres (|-separe) : on garde l'ordre de 1re apparition et on
; ajoute les nouvelles a la fin -> ne bouge PAS quand on active une fenetre
; (≈ ordre de la barre des taches). Le pop-up rembobine dans l'ordre inverse.
Global $g_sWinOrder = "|"
Global $g_iSweepMs   = 40   ; balayage : delai entre 2 activations (bas=rapide ; <30 l'OS peut sauter des fenetres)
Global $g_iLastSweep = 0     ; dernier id de balayage traite (dedup)
; =========================== FIN CONFIG ==================================== ;

Global Const $DIR_N = 0, $DIR_S = 1, $DIR_E = 2, $DIR_O = 3

; etat de pilotage (rempli par job)
Global $g_sAccount = ""   ; label de suivi dans /live/state (ex "C2")
Global $g_sWinName = ""   ; nom du perso = sous-chaine du titre de fenetre (ex "Styxh-[Gal]")
Global $g_iDestX = 0, $g_iDestY = 0
Global $g_bAbort = False   ; ESC pendant un job -> abandonne CE job, daemon reste en vie
Global $g_iLastFocus = 0   ; dernier id de demande de focus traitee (clic perso sur la carte)

; ESC = stoppe le deplacement en cours (le daemon continue de tourner).
; Ctrl+Alt+Q = quitte completement le daemon.
HotKeySet("{ESC}", "_AbortJob")
HotKeySet("^!q", "_Quit")
Global $g_sLog = @ScriptDir & "\dofus_walker.log"

_log("=== daemon walker demarre — pilote depuis live.html (/ui/live.html) ===")

Local $sHealth = _httpGet($g_sApi & "/health")
If @error Or StringInStr($sHealth, "ok") = 0 Then
    _log("!! API injoignable")
    MsgBox(48, "dofus_walker", "API injoignable. Docker up ? port 8000 ?")
    Exit
EndIf
_log("API OK. En attente d'un job (clique un compte -> une case dans live.html).")

; ============================= BOUCLE DAEMON ================================ ;
While 1
    Local $sJob = _httpGet($g_sApi & "/walk/job")
    If @error Then
        _idle("API injoignable — reconnexion…")
        Sleep($g_iIdlePollMs)
        ContinueLoop
    EndIf

    _checkFocus()   ; clic perso sur la carte -> WinActivate sa fenetre
    _maybeReportWindows()   ; board : liste des fenetres Dofus ouvertes
    _checkSweep()   ; pop-up : balayage (activer toutes les fenetres une par une)

    Local $iId = _jobInt($sJob, "id")
    If @error Then
        _idle("Aucun job. Clique un compte puis une case dans live.html.")
        Sleep($g_iIdlePollMs)
        ContinueLoop
    EndIf
    Local $sState = _jobStr($sJob, "state")
    If $sState <> "pending" And $sState <> "running" Then
        _idle("Job termine (" & $sState & "). En attente d'un nouveau.")
        Sleep($g_iIdlePollMs)
        ContinueLoop
    EndIf

    ; --- job de DONJON : clique une cellule de sortie sur chaque fenetre --- ;
    ; (dungeon.html : "Sortir l'equipe -> salle suivante"). Combat manuel ;
    ; ici on ne fait que le pas de porte, pour toute l'equipe.
    If _jobStr($sJob, "kind") = "dungeon_step" Then
        $g_bAbort = False
        _runDungeonStep($iId, $sJob)
        Sleep($g_iIdlePollMs)
        ContinueLoop
    EndIf

    ; --- adoption du job -------------------------------------------------- ;
    Local $aStart = _jobPair($sJob, "start")
    Local $aDest = _jobPair($sJob, "dest")
    If @error Then
        Sleep($g_iIdlePollMs)
        ContinueLoop
    EndIf
    $g_iDestX = $aDest[0]
    $g_iDestY = $aDest[1]

    ToolTip("")
    Local $sLbl = _resolveAccountByPos($aStart[0] & "," & $aStart[1])
    If $sLbl = "" Then
        _log("!! job " & $iId & " : aucun perso a [" & $aStart[0] & "," & $aStart[1] & "]")
        _report($iId, "failed", "perso introuvable a [" & $aStart[0] & "," & $aStart[1] & "] (bouge-le en jeu)", "", "", "")
        Sleep($g_iIdlePollMs)
        ContinueLoop
    EndIf
    $g_sAccount = $sLbl
    $g_sWinName = _jobStr($sJob, "label")   ; nom du perso pour activer la bonne fenetre
    $g_bAbort = False   ; repart propre (ESC d'un job precedent ne doit pas tuer celui-ci)
    _log("=== job " & $iId & " : '" & $sLbl & "' [" & $aStart[0] & "," & $aStart[1] & "] -> [" & $g_iDestX & "," & $g_iDestY & "] ===")
    _runJob($iId)
WEnd

; ============================= UN JOB ====================================== ;
Func _runJob($iId)
    _report($iId, "running", "demarrage — mets la fenetre du perso au 1er plan", "", "", "")
    Local $iStuck = 0
    While 1
        ; ESC local -> abandonne ce job, reste en veille
        If $g_bAbort Then
            $g_bAbort = False
            _log("job " & $iId & " abandonne (ESC).")
            _report($iId, "canceled", "abandonne localement (ESC)", "", "", "")
            Return
        EndIf
        _checkFocus()   ; clic perso sur la carte -> WinActivate (meme pendant un trajet)
        ; annulation / remplacement du job ?
        Local $sJob = _httpGet($g_sApi & "/walk/job")
        If Not @error Then
            Local $iCur = _jobInt($sJob, "id")
            If @error Or $iCur <> $iId Then
                _log("job " & $iId & " remplace/supprime — retour en veille.")
                Return
            EndIf
            If _jobStr($sJob, "state") = "canceled" Then
                _log("job " & $iId & " annule par l'utilisateur.")
                Return
            EndIf
        EndIf

        Local $aPos = _currentMap()
        If @error Then
            _report($iId, "running", "perso non vu dans /live/state — attente…", "", "", "")
            Sleep(1500)
            ContinueLoop
        EndIf
        Local $iX = $aPos[0], $iY = $aPos[1], $iMap = $aPos[2]

        If $iX = $g_iDestX And $iY = $g_iDestY Then
            _log("### ARRIVE [" & $iX & "," & $iY & "] (map " & $iMap & ").")
            _report($iId, "done", "arrive a destination [" & $iX & "," & $iY & "]", $iX, $iY, $iMap)
            Return
        EndIf

        Local $iDir = _nextDir($iX, $iY)
        If @error Then
            If @error = 2 Then
                _report($iId, "failed", "[" & $iX & "," & $iY & "] -> [" & $g_iDestX & "," & $g_iDestY & "] injoignable (grille)", $iX, $iY, $iMap)
                Return
            EndIf
            _report($iId, "running", "route indisponible — attente…", $iX, $iY, $iMap)
            Sleep(1500)
            ContinueLoop
        EndIf

        Local $sDir = _dirName($iDir)
        _log("map [" & $iX & "," & $iY & "] (id " & $iMap & ") -> " & $sDir)
        _report($iId, "running", "map [" & $iX & "," & $iY & "] -> sortie " & $sDir, $iX, $iY, $iMap)

        If _clickExit($iMap, $sDir) And _waitMapChange($iMap, $g_iChangeToMs) Then
            $iStuck = 0
        Else
            $iStuck += 1
            _log("!! pas de changement (bloque " & $iStuck & "x).")
            If $iStuck >= 3 Then
                _report($iId, "failed", "bloque sur map " & $iMap & " (sortie " & $sDir & " ? fenetre au 1er plan ?)", $iX, $iY, $iMap)
                Return
            EndIf
        EndIf
        Sleep(300)
    WEnd
EndFunc

; ===================== UN PAS DE DONJON (equipe) =========================== ;
; Clique la cellule de sortie $cell sur CHAQUE fenetre de l'equipe (par nom de
; perso = sous-chaine du titre). Toutes les fenetres des clients sont supposees
; superposees a la meme position ecran (meme calage cellule->pixel que _clickExit).
; A appeler une fois la salle vaincue : fait passer les 8 a la salle suivante.
Func _runDungeonStep($iId, $sJob)
    Local $aCells = _jobIntArray($sJob, "cells")
    If @error Or UBound($aCells) = 0 Then
        ; compat : ancien champ "cell" (case unique)
        Local $c = _jobInt($sJob, "cell")
        If @error Then
            _report($iId, "failed", "aucune case de sortie", "", "", "")
            Return
        EndIf
        Local $t[1] = [$c]
        $aCells = $t
    EndIf
    Local $iMap = _jobInt($sJob, "target_map")   ; map attendue (indicatif)
    Local $aTeam = _jobStrArray($sJob, "team")
    If @error Or UBound($aTeam) = 0 Then
        _report($iId, "failed", "equipe vide", "", "", $iMap)
        Return
    EndIf
    Local $iN = UBound($aTeam), $iK = UBound($aCells)
    _log("=== dungeon_step " & $iId & " : " & $iN & " fenetre(s), " & $iK & " case(s) (map " & $iMap & ") ===")
    _report($iId, "running", "sortie salle : " & $iN & " fenetre(s), " & $iK & " case(s)", "", "", $iMap)
    For $i = 0 To $iN - 1
        If $g_bAbort Then
            $g_bAbort = False
            _report($iId, "canceled", "abandonne localement (ESC)", "", "", $iMap)
            Return
        EndIf
        ; annulation / remplacement cote serveur ?
        Local $sCur = _httpGet($g_sApi & "/walk/job")
        If Not @error Then
            Local $iCurId = _jobInt($sCur, "id")
            If @error Or $iCurId <> $iId Or _jobStr($sCur, "state") = "canceled" Then
                _log("dungeon_step " & $iId & " annule/remplace — stop.")
                Return
            EndIf
        EndIf
        Local $sWin = $aTeam[$i]
        _report($iId, "running", "fenetre " & ($i + 1) & "/" & $iN & " : " & $sWin, "", "", $iMap)
        If WinActivate($sWin) = 0 Then
            _log("   fenetre '" & $sWin & "' introuvable — on passe.")
        Else
            WinWaitActive($sWin, "", 2)
            Sleep(250)
        EndIf
        ; rejoue le parcours : une case apres l'autre (contourne trous/obstacles)
        For $k = 0 To $iK - 1
            If $g_bAbort Then
                $g_bAbort = False
                _report($iId, "canceled", "abandonne localement (ESC)", "", "", $iMap)
                Return
            EndIf
            Local $sx, $sy
            _cellToScreen($aCells[$k], $sx, $sy)
            MouseMove($sx, $sy, Random(10, 22, 1))
            Sleep(Random(80, 180, 1))
            MouseDown("left")
            Sleep(Random(40, 90, 1))
            MouseUp("left")
            ; entre deux cases : laisser le perso marcher ; apres la derniere : delai standard
            If $k < $iK - 1 Then
                Sleep($g_iStepWalkMs + Random(0, 400, 1))
            Else
                Sleep($g_iAfterClickMs + Random(0, 400, 1))
            EndIf
        Next
    Next
    _report($iId, "done", "equipe sortie (" & $iK & " case(s))", "", "", $iMap)
EndFunc

; ============================= FONCTIONS =================================== ;

; Cellule (0-559) -> grille (gx,gy), formule Dofus 1.29 mapWidth=15.
Func _cellGrid($cell, ByRef $gx, ByRef $gy)
    Local $w = $MAP_WIDTH
    Local $loc5 = Int($cell / (2 * $w - 1))
    Local $loc6 = $cell - $loc5 * (2 * $w - 1)
    Local $loc7 = Mod($loc6, $w)
    $gy = $loc5 - $loc7
    $gx = Int(($cell - ($w - 1) * $gy) / $w)
EndFunc

; Cellule -> pixel ecran (affine calee).
Func _cellToScreen($cell, ByRef $sx, ByRef $sy)
    Local $gx, $gy
    _cellGrid($cell, $gx, $gy)
    $sx = Round($g_aCX[0] * $gx + $g_aCX[1] * $gy + $g_aCX[2])
    $sy = Round($g_aCY[0] * $gx + $g_aCY[1] * $gy + $g_aCY[2])
EndFunc

; Cellule de sortie (0-559) de map $mapId direction $dir ("N"/"S"/"E"/"O").
Func _exitCell($mapId, $dir)
    Local $j = _httpGet($g_sApi & "/map/exit?map_id=" & $mapId & "&dir=" & $dir)
    If @error Then Return SetError(1, 0, -1)
    Local $a = StringRegExp($j, '"cell"\s*:\s*(\d+)', 1)
    If @error Then Return SetError(2, 0, -1)
    Return Int($a[0])
EndFunc

; Clique la cellule de sortie de $mapId vers $dir. False si inconnue.
Func _clickExit($mapId, $dir)
    Local $cell = _exitCell($mapId, $dir)
    If @error Then
        _log("   sortie " & $dir & " inconnue (map " & $mapId & ")")
        Return False
    EndIf
    Local $sx, $sy
    _cellToScreen($cell, $sx, $sy)
    _log("   sortie " & $dir & " = cellule " & $cell & " -> ecran (" & $sx & "," & $sy & ")")
    _activateGame()
    MouseMove($sx, $sy, Random(10, 22, 1))
    Sleep(Random(80, 180, 1))
    MouseDown("left")
    Sleep(Random(40, 90, 1))
    MouseUp("left")
    Sleep($g_iAfterClickMs + Random(0, 400, 1))
    Return True
EndFunc

; Amene la fenetre du client au 1er plan par le NOM DU PERSO (sous-chaine du
; titre). Sans ca, le clic tomberait sur la fenetre active (navigateur...).
Func _activateGame()
    If Not $g_bActivateWin Or $g_sWinName = "" Then Return
    If WinActive($g_sWinName) Then Return
    If WinActivate($g_sWinName) = 0 Then
        _log("   (fenetre '" & $g_sWinName & "' introuvable — clic sans activation)")
        Return
    EndIf
    WinWaitActive($g_sWinName, "", 2)
    Sleep(250)
EndFunc

; Demande de focus posee par live.html (clic sur un perso) : active sa fenetre.
Func _checkFocus()
    Local $j = _httpGet($g_sApi & "/walk/focus")
    If @error Then Return
    Local $aId = StringRegExp($j, '"id"\s*:\s*(\d+)', 1)
    If @error Then Return
    Local $iId = Int($aId[0])
    If $iId <= $g_iLastFocus Then Return
    $g_iLastFocus = $iId
    Local $aNm = StringRegExp($j, '"name"\s*:\s*"([^"]*)"', 1)
    If @error Then Return
    If $aNm[0] <> "" Then
        _activateWin($aNm[0])
        _log("focus (clic carte) -> " & $aNm[0])
    EndIf
EndFunc

; Active une fenetre de maniere robuste (le verrou de 1er plan est deja desactive
; au demarrage ; ici retry + coup d'ALT en secours si jamais ca resiste).
Func _activateWin($title)
    Local $h = WinGetHandle($title)
    If @error Then Return False
    If WinActive($h) Then Return True
    WinActivate($h)
    WinWaitActive($h, "", 1)
    If Not WinActive($h) Then
        Send("{LALT}")
        WinActivate($h)
        WinWaitActive($h, "", 1)
    EndIf
    Return WinActive($h)
EndFunc

; Rapporte au serveur la liste des fenetres Dofus ouvertes (noms de perso), pour
; board.html — la VRAIE liste des clients, meme ceux que le sniffer ne voit pas
; (parques, immobiles). Throttle a $g_iWinReportMs.
Func _maybeReportWindows()
    If $g_iLastWinReport <> 0 And TimerDiff($g_iLastWinReport) < $g_iWinReportMs Then Return
    $g_iLastWinReport = TimerInit()
    Local $aList = WinList()
    If @error Then Return
    ; 1) noms courants (dedup) : set |A|B| + liste ordonnee WinList
    Local $sCurSet = "|", $sCurOrdered = ""
    For $i = 1 To $aList[0][0]
        Local $t = $aList[$i][0]
        If $t = "" Then ContinueLoop
        ; vrai client = "Nom-[Guilde] - Dofus Retro vX" -> exige le separateur " - Dofus Retro"
        ; (exclut l'onglet navigateur "Dofus Retro — Comptes" et le launcher)
        If StringInStr($t, " - Dofus Retro") = 0 Then ContinueLoop
        Local $p = StringInStr($t, " - ")
        Local $nm = ($p > 0) ? StringStripWS(StringLeft($t, $p - 1), 3) : $t
        If $nm = "" Then ContinueLoop
        If StringInStr($sCurSet, "|" & $nm & "|") Then ContinueLoop   ; deja compte
        $sCurSet &= $nm & "|"
        $sCurOrdered &= $nm & "|"
    Next
    ; 2) ordre STABLE : garder l'ordre connu (fenetres toujours la), puis ajouter
    ; les nouvelles a la fin -> l'ordre ne change pas quand on active une fenetre.
    Local $sNew = "|"
    Local $aOld = StringSplit($g_sWinOrder, "|", 2)
    For $k = 0 To UBound($aOld) - 1
        Local $o = $aOld[$k]
        If $o <> "" And StringInStr($sCurSet, "|" & $o & "|") And StringInStr($sNew, "|" & $o & "|") = 0 Then _
                $sNew &= $o & "|"
    Next
    Local $aCur = StringSplit($sCurOrdered, "|", 2)
    For $k = 0 To UBound($aCur) - 1
        Local $c = $aCur[$k]
        If $c <> "" And StringInStr($sNew, "|" & $c & "|") = 0 Then $sNew &= $c & "|"
    Next
    $g_sWinOrder = $sNew
    ; 3) JSON dans l'ordre stable
    Local $aFinal = StringSplit($sNew, "|", 2)
    Local $sNames = "", $n = 0
    For $k = 0 To UBound($aFinal) - 1
        If $aFinal[$k] = "" Then ContinueLoop
        $sNames &= ($n > 0 ? "," : "") & '"' & _jsonEsc($aFinal[$k]) & '"'
        $n += 1
    Next
    _httpPost($g_sApi & "/walk/windows", '{"names":[' & $sNames & ']}')
EndFunc

; Balayage demande par le pop-up : active CHAQUE fenetre de la liste, une par une
; (ordre fourni par le pop-up, ex. inverse de la barre). Dedup par id.
Func _checkSweep()
    Local $j = _httpGet($g_sApi & "/walk/sweep")
    If @error Then Return
    Local $aId = StringRegExp($j, '"id"\s*:\s*(\d+)', 1)
    If @error Then Return
    Local $iId = Int($aId[0])
    If $iId <= $g_iLastSweep Then Return
    $g_iLastSweep = $iId
    Local $aNames = _sweepNames($j)
    If @error Or UBound($aNames) = 0 Then Return
    _log("=== balayage : " & UBound($aNames) & " fenetre(s) ===")
    For $i = 0 To UBound($aNames) - 1
        If $g_bAbort Then
            $g_bAbort = False
            _log("   balayage interrompu (ESC).")
            Return
        EndIf
        ; activation RAPIDE : pas de WinWaitActive (le verrou de 1er plan est deja
        ; desactive) -> on enchaine sans attendre 1s par fenetre.
        WinActivate($aNames[$i])
        Sleep($g_iSweepMs)
    Next
    _log("   balayage termine.")
EndFunc

; extrait le tableau "names" d'une reponse de balayage. Les noms peuvent contenir
; des crochets ("Styxh-[Gal]") -> on borne la fin du tableau sur "]}" (fin d'objet).
Func _sweepNames($sJson)
    Local $a = StringRegExp($sJson, '"names"\s*:\s*\[(.*?)\]\s*\}', 1)
    If @error Then
        Local $z[0]
        Return SetError(1, 0, $z)
    EndIf
    Local $aStr = StringRegExp($a[0], '"([^"]*)"', 3)
    If @error Then
        Local $z0[0]
        Return SetError(2, 0, $z0)
    EndIf
    Return $aStr
EndFunc

Func _nextDir($x, $y)
    Local $u = $g_sApi & "/route/path?fx=" & $x & "&fy=" & $y & "&tx=" & $g_iDestX & "&ty=" & $g_iDestY
    Local $j = _httpGet($u)
    If @error Then Return SetError(1, 0, -1)
    Local $aR = StringRegExp($j, '"reachable"\s*:\s*(true|false)', 1)
    If Not @error And $aR[0] = "false" Then Return SetError(2, 0, -1)
    Local $aN = StringRegExp($j, '"next"\s*:\s*"([NSEO])"', 1)
    If @error Then Return -1
    Switch $aN[0]
        Case "N"
            Return $DIR_N
        Case "S"
            Return $DIR_S
        Case "E"
            Return $DIR_E
        Case "O"
            Return $DIR_O
    EndSwitch
    Return -1
EndFunc

Func _dirName($d)
    Switch $d
        Case $DIR_N
            Return "N"
        Case $DIR_S
            Return "S"
        Case $DIR_E
            Return "E"
        Case $DIR_O
            Return "O"
    EndSwitch
    Return "?"
EndFunc

Func _waitMapChange($iFromMap, $iTimeoutMs)
    Local $t = TimerInit()
    While TimerDiff($t) < $iTimeoutMs
        If $g_bAbort Then Return False
        Sleep($g_iPollMs)
        Local $aPos = _currentMap()
        If Not @error Then
            If $aPos[2] <> $iFromMap Then
                _log("   -> nouvelle map id " & $aPos[2] & " [" & $aPos[0] & "," & $aPos[1] & "]")
                Return True
            EndIf
        EndIf
    WEnd
    Return False
EndFunc

; Trouve le label du compte dont la coord = "x,y" dans /live/state. "" si absent.
Func _resolveAccountByPos($sXY)
    Local $j = _httpGet($g_sApi & "/live/state")
    If @error Then Return ""
    Local $a = StringRegExp($j, '"label"\s*:\s*"([^"]+)"[^}]*?"coord"\s*:\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]', 4)
    If @error Then Return ""
    For $i = 0 To UBound($a) - 1
        Local $m = $a[$i]
        If ($m[2] & "," & $m[3]) = $sXY Then Return $m[1]
    Next
    Return ""
EndFunc

Func _currentMap()
    Local $sJson = _httpGet($g_sApi & "/live/state")
    If @error Then Return SetError(1, 0, 0)
    Local $iPos = StringInStr($sJson, '"accounts"')
    If $iPos = 0 Then Return SetError(2, 0, 0)
    Local $sAcc = StringMid($sJson, $iPos)
    If $g_sAccount <> "" Then
        Local $iSel = StringInStr($sAcc, '"' & $g_sAccount)
        If $iSel = 0 Then Return SetError(5, 0, 0)
        $sAcc = StringMid($sAcc, $iSel)
    EndIf
    Local $aMap = StringRegExp($sAcc, '"map_id"\s*:\s*(-?\d+)', 1)
    If @error Then Return SetError(3, 0, 0)
    Local $aCo = StringRegExp($sAcc, '"coord"\s*:\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]', 1)
    If @error Then
        Local $aRet[3] = [9999, 9999, Number($aMap[0])]
        Return SetError(4, 0, $aRet)
    EndIf
    Local $aRet[3] = [Number($aCo[0]), Number($aCo[1]), Number($aMap[0])]
    Return $aRet
EndFunc

; --- parsing job JSON ------------------------------------------------------ ;
Func _jobInt($sJson, $sKey)
    Local $a = StringRegExp($sJson, '"' & $sKey & '"\s*:\s*(-?\d+)', 1)
    If @error Then Return SetError(1, 0, 0)
    Return Int($a[0])
EndFunc

Func _jobStr($sJson, $sKey)
    Local $a = StringRegExp($sJson, '"' & $sKey & '"\s*:\s*"([^"]*)"', 1)
    If @error Then Return ""
    Return $a[0]
EndFunc

; renvoie [x, y] pour une cle "start"/"dest" ; @error si absente
Func _jobPair($sJson, $sKey)
    Local $a = StringRegExp($sJson, '"' & $sKey & '"\s*:\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]', 1)
    If @error Then
        Local $z[2] = [0, 0]
        Return SetError(1, 0, $z)
    EndIf
    Local $r[2] = [Number($a[0]), Number($a[1])]
    Return $r
EndFunc

; renvoie un tableau de chaines pour une cle tableau JSON (ex "team").
; La reponse est compacte (sans espaces) ; les noms de perso peuvent contenir
; des crochets ("Styxh-[Gal]") -> on borne sur la cle suivante "target_map".
Func _jobStrArray($sJson, $sKey)
    Local $a = StringRegExp($sJson, '"' & $sKey & '"\s*:\s*\[(.*?)\]\s*,\s*"target_map"', 1)
    If @error Then
        Local $z[0]
        Return SetError(1, 0, $z)
    EndIf
    Local $aStr = StringRegExp($a[0], '"([^"]*)"', 3)
    If @error Then
        Local $z0[0]
        Return SetError(2, 0, $z0)
    EndIf
    Return $aStr
EndFunc

; renvoie un tableau d'entiers pour une cle tableau JSON (ex "cells").
; Les entiers ne contiennent pas de crochet -> bornage simple sur ']'.
Func _jobIntArray($sJson, $sKey)
    Local $a = StringRegExp($sJson, '"' & $sKey & '"\s*:\s*\[([^\]]*)\]', 1)
    If @error Then
        Local $z[0]
        Return SetError(1, 0, $z)
    EndIf
    Local $aNums = StringRegExp($a[0], '-?\d+', 3)
    If @error Then
        Local $z0[0]
        Return SetError(2, 0, $z0)
    EndIf
    For $i = 0 To UBound($aNums) - 1
        $aNums[$i] = Number($aNums[$i])
    Next
    Return $aNums
EndFunc

; --- rapport d'avancement (POST /walk/status) ------------------------------ ;
Func _report($iId, $sState, $sMsg, $x, $y, $iMap)
    Local $sBody = '{"job_id":' & $iId & ',"state":"' & $sState & '","message":"' & _jsonEsc($sMsg) & '"'
    If $x <> "" And $y <> "" Then
        $sBody &= ',"x":' & $x & ',"y":' & $y
    EndIf
    If $iMap <> "" Then
        $sBody &= ',"map_id":' & $iMap
    EndIf
    $sBody &= '}'
    _httpPost($g_sApi & "/walk/status", $sBody)
EndFunc

Func _jsonEsc($s)
    $s = StringReplace($s, '\', '\\')
    $s = StringReplace($s, '"', '\"')
    Return $s
EndFunc

Func _idle($sMsg)
    ToolTip($sMsg & "  (ESC = stop deplacement · Ctrl+Alt+Q = quitter)", 30, 30, "dofus_walker")
EndFunc

Func _httpGet($url)
    Local $o = ObjCreate("winhttp.winhttprequest.5.1")
    If Not IsObj($o) Then Return SetError(1, 0, "")
    Local $oErr = ObjEvent("AutoIt.Error", "_comSilent")
    $o.Open("GET", $url, False)
    $o.SetTimeouts(2000, 2000, 3000, 5000)
    $o.Send()
    If @error Then
        $oErr = 0
        Return SetError(2, 0, "")
    EndIf
    Local $s = $o.ResponseText
    $oErr = 0
    Return $s
EndFunc

Func _httpPost($url, $body)
    Local $o = ObjCreate("winhttp.winhttprequest.5.1")
    If Not IsObj($o) Then Return SetError(1, 0, "")
    Local $oErr = ObjEvent("AutoIt.Error", "_comSilent")
    $o.Open("POST", $url, False)
    $o.SetRequestHeader("Content-Type", "application/json")
    $o.SetTimeouts(2000, 2000, 3000, 5000)
    $o.Send($body)
    If @error Then
        $oErr = 0
        Return SetError(2, 0, "")
    EndIf
    Local $s = $o.ResponseText
    $oErr = 0
    Return $s
EndFunc

Func _comSilent()
EndFunc

Func _log($sMsg)
    Local $sLine = @HOUR & ":" & @MIN & ":" & @SEC & "  " & $sMsg
    ConsoleWrite($sLine & @CRLF)
    FileWrite($g_sLog, $sLine & @CRLF)
EndFunc

; ESC : abandonne le job courant, mais NE quitte PAS le daemon.
Func _AbortJob()
    $g_bAbort = True
    _log(">> ESC : abandon du deplacement courant (le daemon reste actif).")
EndFunc

; Ctrl+Alt+Q : quitte completement le daemon.
Func _Quit()
    _log("=== QUIT (Ctrl+Alt+Q) ===")
    Exit
EndFunc
