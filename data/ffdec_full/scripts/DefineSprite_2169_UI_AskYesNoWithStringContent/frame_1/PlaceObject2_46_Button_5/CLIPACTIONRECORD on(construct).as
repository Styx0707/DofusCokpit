on(construct){
   while(true)
   {
      if(!(0x24200691 | 0x24200691))
      {
         if(!ord("\x07"))
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
         if(!(getTimer() + 1))
         {
            §§push(getProperty(§§pop(), _X));
         }
         backgroundDown = "ButtonNormalDown";
         backgroundUp = "ButtonNormalUp";
         enabled = true;
         icon = "";
         label = "";
         selected = false;
         §§push("styleName");
         §§push("OrangeButton");
         if(!ord("\x04"))
         {
            var §§pop() = §§pop();
            §§goto(addr1456d);
         }
      }
      set(§§pop(),§§pop());
      set(§§constant(11),false);
      break;
   }
   addr1456d:
}
