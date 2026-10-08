on(construct){
   while(true)
   {
      if(!(true or true))
      {
         if(!(true and true))
         {
            break;
         }
      }
      else
      {
         §§push("\x05");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      backgroundDown = "ButtonJoinTaxCollectorDown";
      backgroundUp = "ButtonJoinTaxCollectorUp";
      enabled = true;
      icon = "TaxCollectorViewerPlayer";
      label = ".";
      §§push("selected");
      §§push(false);
      if(!ord("\n"))
      {
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr107df);
      }
      break;
   }
   set(§§pop(),§§pop());
   styleName = "none";
   toggle = false;
   addr107df:
}
