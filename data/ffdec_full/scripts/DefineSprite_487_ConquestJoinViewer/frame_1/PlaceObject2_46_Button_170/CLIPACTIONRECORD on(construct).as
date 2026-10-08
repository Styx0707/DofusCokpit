on(construct){
   while(true)
   {
      if(!ord("\x07"))
      {
         if(!ord("\x07"))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(_temp_1 and _temp_1)
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
            §§goto(addr31e4e);
         }
      }
      set(§§pop(),§§pop());
      §§push("styleName");
      §§push("none");
      break;
   }
   set(§§pop(),§§pop());
   toggle = false;
   addr31e4e:
}
