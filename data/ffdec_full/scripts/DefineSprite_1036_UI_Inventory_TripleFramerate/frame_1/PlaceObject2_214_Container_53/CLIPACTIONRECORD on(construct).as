on(construct){
   while(true)
   {
      if(!ord("\x06"))
      {
         if(!(0x2C8335FB & 0x2C8335FB))
         {
            break;
         }
      }
      else
      {
         §§push(319251582);
      }
      if(§§pop() - 1)
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
            §§goto(addr1ba3a);
         }
      }
      set(§§pop(),§§pop());
      id = 1;
      break;
   }
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr1ba3a:
   getProperty(§§pop(), _X);
}
