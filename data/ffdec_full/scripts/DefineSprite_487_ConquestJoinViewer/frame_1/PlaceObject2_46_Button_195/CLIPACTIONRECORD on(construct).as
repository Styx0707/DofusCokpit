on(construct){
   while(true)
   {
      if(!(true or true))
      {
         if(!ord("\x0b"))
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
         backgroundDown = "ButtonJoinTaxCollectorDown";
         backgroundUp = "ButtonJoinTaxCollectorUp";
         enabled = true;
         icon = "TaxCollectorViewerPlayer";
         label = ".";
         §§push("selected");
         §§push(false);
         if(!(getTimer() + 1))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr3dda4);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   styleName = "none";
   toggle = false;
   addr3dda4:
}
