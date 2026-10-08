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
         §§push("\b");
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
         if(!ord("\x07"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr3a31e);
         }
      }
      set(§§pop(),§§pop());
      §§push("styleName");
      §§push("none");
      break;
   }
   set(§§pop(),§§pop());
   toggle = false;
   addr3a31e:
}
