on(construct){
   while(true)
   {
      if(!(0x351FFEF6 | 0x351FFEF6))
      {
         if(!(0x351FFEF6 & 0x351FFEF6))
         {
            break;
         }
      }
      else
      {
         §§push("\x05");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_InventoryContainerHighlight");
         if(!getTimer())
         {
            §§pop()[§§pop()] = §§pop();
            §§goto(addr1d28a);
         }
      }
      set(§§pop(),§§pop());
      §§push("margin");
      §§push(2);
      break;
   }
   set(§§pop(),§§pop());
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr1d28a:
}
