on(construct){
   while(true)
   {
      if(!(0x044C78B8 | 0x044C78B8))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      backgroundRenderer = "UI_ShortcutsPanelContainerBackground";
      set("\x16\x10\x12","UI_ShortcutsPanelContainerBorder");
      dragAndDrop = true;
      enabled = true;
      set("\x18\x07\x0e",true);
      §§push("highlightRenderer");
      §§push("UI_ShortcutsPanelContainerHighlight");
      if(!(getTimer() + 1))
      {
         duplicateMovieClip(§§pop(),§§pop(),§§pop());
      }
      else
      {
         addr2d3ba:
         set(§§pop(),§§pop());
         id = 1;
         margin = 1;
         set("\x1a\x1e\b",false);
         styleName = "InventoryGridContainer";
      }
      return;
   }
   §§goto(addr2d3ba);
}
