on(construct){
   while(true)
   {
      if(!ord("\x0b"))
      {
         if(!(0x2778EF03 & 0x2778EF03))
         {
            break;
         }
      }
      else
      {
         §§push(671154144);
      }
      if(!(§§pop() + 1))
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
      if(!getTimer())
      {
         setProperty(§§pop(), _X, §§pop());
      }
      else
      {
         addr1273f:
         set(§§pop(),§§pop());
         id = 1;
         margin = 2;
         set("\x1a\x1e\b",false);
         styleName = "default";
      }
      return;
   }
   §§goto(addr1273f);
}
