on(construct){
   while(true)
   {
      if(!(true or true))
      {
         if(!ord("\x04"))
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
         backgroundDown = "ButtonJoinTaxCollectorDown";
         backgroundUp = "ButtonJoinTaxCollectorUp";
         enabled = true;
         icon = "TaxCollectorViewerPlayer";
         label = ".";
         selected = false;
         §§push("styleName");
         §§push("none");
         if(!(getTimer() + 1))
         {
            §§goto(addr288f);
         }
      }
      set(§§pop(),§§pop());
      toggle = false;
      break;
   }
   addr288f:
   getProperty(§§pop(), _X);
}
