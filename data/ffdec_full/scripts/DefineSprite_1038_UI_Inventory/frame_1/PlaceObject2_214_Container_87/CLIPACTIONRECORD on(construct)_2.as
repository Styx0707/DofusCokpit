on(construct){
   while(true)
   {
      if(!ord("\x06"))
      {
         if(!(0x3030E9EB & 0x3030E9EB))
         {
            break;
         }
      }
      else
      {
         §§push(76700856);
      }
      if(§§pop())
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(true);
         if(false)
         {
            §§goto(addr10a4e);
         }
      }
      set(§§pop(),§§pop());
      highlightRenderer = "UI_InventoryContainerHighlight";
      break;
   }
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr10a4e:
   getProperty(§§pop(), _X);
}
