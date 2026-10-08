on(construct){
   while(true)
   {
      if(!(0x088E6D08 | 0x088E6D08))
      {
         if(!(0x088E6D08 | 0x088E6D08))
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
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(true);
         if(!getTimer())
         {
            §§pop()[§§pop()] = §§pop();
            §§goto(addr15d06);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   highlightRenderer = "UI_InventoryContainerHighlight";
   id = 1;
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr15d06:
}
