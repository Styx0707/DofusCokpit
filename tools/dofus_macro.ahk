; ============================================================================
;  Dofus Retro (serveur prive) - Macro multibox captures (arene)
;    F7  = CALIBRAGE : coords sous la souris
;    F9  = LANCER : aggro -> join epee -> placement Cra -> Pret
;    F10 = Cra : double explo
;    F11 = DIAGNOSTIC epee (ImageSearch)
;    F12 = quitter
;  AutoHotkey v1.1.
; ============================================================================
#SingleInstance Force
#NoEnv
SendMode Input
SetTitleMatchMode, 2
CoordMode, Mouse, Client
CoordMode, Pixel, Client

; ================================ CONFIG ====================================
WIN_MATCH   := "Dofus Retro"

; -- 1) AGGRO (clic droit) --
AGGRO_TITLE := "Styxh-[Gal]"
AGGRO_X     := 1431
AGGRO_Y     := 842
DELAI_JOIN  := 1500

; -- 2) JOIN : rejoindre TON combat via l'EPEE (cherchee dans une ZONE) --
;    ZONE_X1/Y1 = coin HAUT-GAUCHE, ZONE_X2/Y2 = coin BAS-DROIT
;    (X1 < X2 et Y1 < Y2 obligatoirement, sinon ImageSearch echoue)
JOIN_MODE   := "image"
JOIN_IMG    := "sword.bmp"
JOIN_TOL    := 100
ZONE_X1     := 1300
ZONE_Y1     := 766
ZONE_X2     := 1434
ZONE_Y2     := 834
JOIN_X      := 1373                 ; secours si epee non vue
JOIN_Y      := 811
DELAI_PLACEMENT := 2000

; -- 3) PLACEMENT obligatoire du Cra --
PLACE_CRA   := true
CRA_PLACE_X := 1427
CRA_PLACE_Y := 918

; -- 4) PRET (clic gauche) --
READY_X     := 2439
READY_Y     := 1023

; -- Cra : explo (a calibrer plus tard avec F7 en combat) --
CRA_TITLE   := "Styxh-[Gal]"
KEY_EXPLO   := "3"
TARGET_X    := 640
TARGET_Y    := 330

DELAI_ACTION  := 300
DELAI_FENETRE := 200
; ===========================================================================

IMG := A_ScriptDir . "\" . JOIN_IMG

FindSword(ByRef fx, ByRef fy) {
    global ZONE_X1, ZONE_Y1, ZONE_X2, ZONE_Y2, JOIN_TOL, IMG
    ImageSearch, fx, fy, %ZONE_X1%, %ZONE_Y1%, %ZONE_X2%, %ZONE_Y2%, % "*" . JOIN_TOL . " " . IMG
    return (ErrorLevel = 0)
}

; ---- F7 : calibrage -------------------------------------------------------
F7::
    MouseGetPos, mx, my
    WinGetActiveTitle, at
    ToolTip, % "X = " . mx . "   Y = " . my . "`n(" . at . ")"
Return

; ---- F11 : DIAGNOSTIC -----------------------------------------------------
F11::
    if !FileExist(IMG) {
        Tip("FICHIER INTROUVABLE :`n" . IMG)
        Return
    }
    ImageSearch, fx, fy, %ZONE_X1%, %ZONE_Y1%, %ZONE_X2%, %ZONE_Y2%, % "*" . JOIN_TOL . " " . IMG
    ez := ErrorLevel
    ImageSearch, gx, gy, 0, 0, A_ScreenWidth, A_ScreenHeight, % "*" . JOIN_TOL . " " . IMG
    eg := ErrorLevel
    if (ez = 0)
        Tip("OK - epee TROUVEE dans la zone : X=" . fx . " Y=" . fy)
    else if (ez = 2 or eg = 2)
        Tip("IMAGE ILLISIBLE (ErrLvl 2) -> sword en BMP 24 bits")
    else if (eg = 0)
        Tip("Epee trouvee HORS zone (X=" . gx . " Y=" . gy . ") -> ajuste ZONE_*")
    else
        Tip("NON trouvee (ErrLvl 1) -> monte JOIN_TOL / recadre sword serre")
Return

; ---- F9 : aggro -> join -> placement Cra -> Pret --------------------------
F9::
    ; 1) AGGRO (clic droit)
    WinActivate, %AGGRO_TITLE%
    WinWaitActive, %AGGRO_TITLE%,, 1
    if ErrorLevel {
        Tip("Fenetre aggro introuvable")
        Return
    }
    Click, %AGGRO_X%, %AGGRO_Y%, Right
    Tip("Aggro...")
    Sleep, %DELAI_JOIN%

    ; 2) JOIN : les autres cliquent l'epee (clic droit)
    WinGet, wins, List, %WIN_MATCH%
    joined := 0
    Loop, %wins% {
        id := wins%A_Index%
        WinGetTitle, ttl, ahk_id %id%
        if InStr(ttl, "Ankama Launcher")
            continue
        if InStr(ttl, AGGRO_TITLE)
            continue
        WinActivate, ahk_id %id%
        WinWaitActive, ahk_id %id%,, 1
        Sleep, 150
        if (JOIN_MODE = "image") {
            if FindSword(fx, fy)
                Click, %fx%, %fy%, Right
            else
                Click, %JOIN_X%, %JOIN_Y%, Right
        } else {
            Click, %JOIN_X%, %JOIN_Y%, Right
        }
        joined++
        Sleep, %DELAI_FENETRE%
    }
    Tip("Joins: " . joined)
    Sleep, %DELAI_PLACEMENT%

    ; 3) PLACEMENT obligatoire du Cra (case fixe)
    if (PLACE_CRA) {
        WinActivate, %CRA_TITLE%
        WinWaitActive, %CRA_TITLE%,, 1
        Click, %CRA_PLACE_X%, %CRA_PLACE_Y%
        Sleep, %DELAI_FENETRE%
    }

    ; 4) PRET sur toutes les fenetres
    n := 0
    Loop, %wins% {
        id := wins%A_Index%
        WinGetTitle, ttl, ahk_id %id%
        if InStr(ttl, "Ankama Launcher")
            continue
        WinActivate, ahk_id %id%
        WinWaitActive, ahk_id %id%,, 1
        Click, %READY_X%, %READY_Y%
        n++
        Sleep, %DELAI_FENETRE%
    }
    Tip("Combat lance (" . n . " Pret)")
Return

; ---- F10 : Cra double explo ----------------------------------------------
F10::
    WinActivate, %CRA_TITLE%
    WinWaitActive, %CRA_TITLE%,, 1
    if ErrorLevel {
        Tip("Fenetre Cra introuvable")
        Return
    }
    Send, %KEY_EXPLO%
    Sleep, %DELAI_ACTION%
    Click, %TARGET_X%, %TARGET_Y%
    Sleep, %DELAI_ACTION%
    Send, %KEY_EXPLO%
    Sleep, %DELAI_ACTION%
    Click, %TARGET_X%, %TARGET_Y%
    Tip("Double explo envoye")
Return

Tip(msg) {
    ToolTip, %msg%
    SetTimer, ClearTip, -2200
}
ClearTip:
    ToolTip
Return

F12::ExitApp
