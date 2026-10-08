on(construct){
   loop1:
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!(0x0848F250 & 0x0848F250))
         {
            break;
         }
      }
      else
      {
         §§push(618678290);
      }
      if(!(§§pop() - 1))
      {
         break;
      }
      addr156da:
      while(true)
      {
         if(!ord("\b"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            break;
         }
         backgroundDown = "ButtonMinimizeDown";
         backgroundUp = "ButtonMinimizeUp";
         enabled = true;
         icon = "";
         label = "";
         selected = false;
         §§push("styleName");
         §§push("OrangeButton");
         break loop1;
         §§push(getProperty(§§pop(), _X));
      }
      return;
   }
   set(§§pop(),§§pop());
   set("\b\x01\x1d{invalid_utf8=150}\x04",false);
   §§goto(addr156da);
}
