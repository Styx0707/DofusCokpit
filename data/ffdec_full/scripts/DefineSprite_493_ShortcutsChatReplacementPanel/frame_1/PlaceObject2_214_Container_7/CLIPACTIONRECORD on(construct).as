on(construct){
   while(true)
   {
      if(!(0x0D4D43AC & 0x0D4D43AC))
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push(399062830);
      }
      if(§§pop())
      {
         backgroundRenderer = "UI_ShortcutsPanelContainerBackground";
         set("\x16\x10\x12","UI_ShortcutsPanelContainerBorder");
         dragAndDrop = true;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(true);
         if(!(getTimer() + 1))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr1cebd);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   highlightRenderer = "UI_ShortcutsPanelContainerHighlight";
   id = 1;
   margin = 1;
   set("\x1a\x1e\b",false);
   styleName = "InventoryGridContainer";
   addr1cebd:
}
