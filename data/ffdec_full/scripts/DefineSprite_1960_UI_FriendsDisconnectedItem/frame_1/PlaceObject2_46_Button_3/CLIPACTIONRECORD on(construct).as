on(construct){
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!ord("\x02"))
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
      backgroundDown = "ButtonSquareDown";
      backgroundUp = "ButtonSquareUp";
      enabled = true;
      icon = "EditSmall";
      label = "";
      §§push("selected");
      §§push(false);
      if(!getTimer())
      {
         §§push(getProperty(§§pop(), _X));
      }
      else
      {
         addr10001:
         set(§§pop(),§§pop());
         styleName = "OrangeButton";
         toggle = false;
      }
      return;
   }
   §§goto(addr10001);
}
