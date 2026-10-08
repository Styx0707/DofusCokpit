on(construct){
   while(true)
   {
      if(!ord("\x06"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(§§pop())
      {
         break;
      }
      backgroundDown = "ButtonNormalDown";
      backgroundUp = "ButtonNormalUp";
      enabled = true;
      icon = "";
      label = "Label";
      §§push("selected");
      §§push(false);
      if(!getTimer())
      {
         §§goto(addr114bf);
      }
      break;
   }
   set(§§pop(),§§pop());
   styleName = "OrangeButton";
   toggle = false;
   addr114bf:
   §§pop()(§§pop());
}
