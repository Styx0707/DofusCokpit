on(construct){
   while(true)
   {
      if(!(0x08D42EDA & 0x08D42EDA))
      {
         if(!ord("\x03"))
         {
            break;
         }
      }
      else
      {
         §§push("\n");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      backgroundDown = "ButtonNormalDown";
      backgroundUp = "ButtonNormalUp";
      enabled = true;
      icon = "";
      §§push("label");
      §§push("Label");
      if(false)
      {
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
      }
      else
      {
         addr13eda:
         set(§§pop(),§§pop());
         selected = false;
         styleName = "OrangeWhiteBorderButton";
         toggle = false;
      }
      return;
   }
   §§goto(addr13eda);
}
