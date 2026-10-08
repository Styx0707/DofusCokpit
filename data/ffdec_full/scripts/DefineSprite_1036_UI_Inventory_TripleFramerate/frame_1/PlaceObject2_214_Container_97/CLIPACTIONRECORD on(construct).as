on(construct){
   while(true)
   {
      if(!ord("\x02"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x06");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(true);
         if(!(getTimer() + 1))
         {
            §§goto(addr6728);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   highlightRenderer = "UI_InventoryContainerHighlight_TripleFramerate";
   id = 1;
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr6728:
   §§pop()(§§pop());
}
