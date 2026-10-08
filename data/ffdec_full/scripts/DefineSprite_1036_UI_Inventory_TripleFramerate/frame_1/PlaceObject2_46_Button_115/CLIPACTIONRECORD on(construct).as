on(construct){
   while(true)
   {
      if(!(0x0194070A | 0x0194070A))
      {
         if(false)
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
         backgroundDown = "ButtonToggleDown";
         backgroundUp = "ButtonToggleUp";
         enabled = true;
         icon = "FilterIcon10";
         label = "";
         §§push("selected");
         §§push(false);
         if(!(getTimer() + 1))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addrffaf);
         }
      }
      set(§§pop(),§§pop());
      styleName = "FilterButton";
      break;
   }
   toggle = true;
   addrffaf:
}
