on(construct){
   while(true)
   {
      if(!ord("\x04"))
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
         backgroundDown = "ButtonJoinTaxCollectorDown";
         backgroundUp = "ButtonJoinTaxCollectorUp";
         enabled = true;
         icon = "TaxCollectorViewerPlayer";
         §§push("label");
         §§push(".");
         if(false)
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr333cb);
         }
      }
      set(§§pop(),§§pop());
      §§push("selected");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   styleName = "none";
   toggle = false;
   addr333cb:
}
