on(construct){
   while(true)
   {
      if(!(0x1B588A15 | 0x1B588A15))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_InventoryContainerHighlight_TripleFramerate");
         if(false)
         {
            §§goto(addr18df6);
         }
      }
      set(§§pop(),§§pop());
      id = 1;
      break;
   }
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr18df6:
   getProperty(§§pop(), _X);
}
