on(construct){
   while(true)
   {
      if(!(0x0CE78AAC | 0x0CE78AAC))
      {
         if(!ord("\t"))
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
         §§push("label");
         §§push(".");
         if(!(getTimer() + 1))
         {
            §§goto(addr2869);
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
   addr2869:
   §§pop()();
}
