on(construct){
   while(true)
   {
      if(false)
      {
         if(!(0x3B44A6FA & 0x3B44A6FA))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 and _temp_1))
      {
         break;
      }
      backgroundRenderer = "UI_InventoryContainerBackground";
      set("\x16\x10\x12","");
      dragAndDrop = true;
      enabled = true;
      §§push("\x18\x07\x0e");
      §§push(true);
      if(!(getTimer() + 1))
      {
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr90b7);
      }
      break;
   }
   set(§§pop(),§§pop());
   highlightRenderer = "UI_InventoryContainerHighlight_TripleFramerate";
   id = 1;
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr90b7:
}
