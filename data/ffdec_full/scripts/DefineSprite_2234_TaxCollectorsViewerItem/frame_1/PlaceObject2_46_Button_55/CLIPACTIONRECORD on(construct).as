on(construct){
   while(true)
   {
      if(!ord("\x05"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         backgroundDown = "ButtonJoinTaxCollectorDown";
         backgroundUp = "ButtonJoinTaxCollectorUp";
         enabled = true;
         icon = "TaxCollectorViewerPlayer";
         §§push("label");
         §§push(".");
         if(!getTimer())
         {
            §§goto(addr12058);
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
   addr12058:
   §§pop()();
}
