on(construct){
   while(true)
   {
      if(!ord("\b"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         backgroundRenderer = "UI_ShortcutsPanelContainerBackground";
         set("\x16\x10\x12","UI_ShortcutsPanelContainerBorder");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_ShortcutsPanelContainerHighlight");
         if(false)
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr8c62);
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
   addr8c62:
}
