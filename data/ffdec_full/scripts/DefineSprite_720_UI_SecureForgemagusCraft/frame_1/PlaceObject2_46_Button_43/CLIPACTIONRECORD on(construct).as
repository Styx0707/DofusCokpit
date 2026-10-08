on(construct){
   while(true)
   {
      if(!ord("\x05"))
      {
         if(!ord("\x05"))
         {
            break;
         }
      }
      else
      {
         §§push(380920113);
      }
      if(§§pop())
      {
         backgroundDown = "ButtonToggleDown";
         backgroundUp = "ButtonToggleUp";
         enabled = true;
         icon = "FilterIcon10";
         label = "";
         §§push("selected");
         §§push(true);
         if(!(getTimer() + 1))
         {
            §§goto(addr1b44f);
         }
      }
      set(§§pop(),§§pop());
      §§push("styleName");
      §§push("FilterButton");
      break;
   }
   set(§§pop(),§§pop());
   toggle = true;
   addr1b44f:
   getProperty(§§pop(), _X);
}
