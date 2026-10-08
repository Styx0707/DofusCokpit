on(construct){
   while(true)
   {
      if(!(true and true))
      {
         if(!(true or true))
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
         §§push("selected");
         §§push(false);
         if(!getTimer())
         {
            §§goto(addr2ef70);
         }
      }
      set(§§pop(),§§pop());
      §§push("styleName");
      §§push("none");
      break;
   }
   set(§§pop(),§§pop());
   toggle = false;
   addr2ef70:
   new §\§\§pop()§();
}
