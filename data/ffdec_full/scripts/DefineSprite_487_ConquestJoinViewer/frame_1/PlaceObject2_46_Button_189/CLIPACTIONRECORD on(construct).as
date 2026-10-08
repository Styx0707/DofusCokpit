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
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 and _temp_1))
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
      if(!getTimer())
      {
         setProperty(§§pop(), _X, §§pop());
      }
      else
      {
         addrdac3:
         set(§§pop(),§§pop());
         styleName = "none";
         toggle = false;
      }
      return;
   }
   §§goto(addrdac3);
}
