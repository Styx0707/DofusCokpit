on(construct){
   while(true)
   {
      if(!ord("\x07"))
      {
         if(!ord("\x07"))
         {
            break;
         }
      }
      else
      {
         §§push(684644937);
      }
      if(§§pop() - 1)
      {
         backgroundRenderer = "UI_ShortcutsPanelContainerBackground";
         set("\x16\x10\x12","UI_ShortcutsPanelContainerBorder");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_ShortcutsPanelContainerHighlight");
         if(!(getTimer() + 1))
         {
            §§goto(addr2bc35);
         }
      }
      set(§§pop(),§§pop());
      §§push("id");
      §§push(1);
      break;
   }
   set(§§pop(),§§pop());
   margin = 1;
   set("\x1a\x1e\b",false);
   styleName = "InventoryGridContainer";
   addr2bc35:
   getProperty(§§pop(), _X);
}
