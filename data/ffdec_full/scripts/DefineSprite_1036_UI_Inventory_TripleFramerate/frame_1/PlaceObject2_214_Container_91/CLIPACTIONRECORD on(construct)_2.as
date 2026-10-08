on(construct){
   while(true)
   {
      if(!(0x26C9CE18 & 0x26C9CE18))
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
      if(§§pop())
      {
         break;
      }
      backgroundRenderer = "UI_InventoryContainerBackground";
      set("\x16\x10\x12","");
      dragAndDrop = true;
      enabled = true;
      set("\x18\x07\x0e",true);
      §§push("highlightRenderer");
      §§push("UI_InventoryContainerHighlight_TripleFramerate");
      if(!ord("\x05"))
      {
         §§goto(addr1ffb);
      }
      break;
   }
   set(§§pop(),§§pop());
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr1ffb:
   getProperty(§§pop(), _X);
}
