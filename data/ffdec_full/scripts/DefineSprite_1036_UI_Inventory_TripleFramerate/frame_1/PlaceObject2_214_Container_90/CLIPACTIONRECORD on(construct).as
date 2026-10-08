on(construct){
   while(true)
   {
      if(!ord("\x05"))
      {
         if(!(0x2BAA6009 & 0x2BAA6009))
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
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
            duplicateMovieClip(§§pop(),§§pop(),§§pop());
            §§goto(addr6ed1);
         }
      }
      set(§§pop(),§§pop());
      id = 1;
      break;
   }
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr6ed1:
}
