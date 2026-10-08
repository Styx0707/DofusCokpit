on(construct){
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!(0x0BE52366 & 0x0BE52366))
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(!(getTimer() + 1))
            {
               setProperty(§§pop(), _X, §§pop());
               break;
            }
            backgroundDown = "ButtonNormalDown";
            backgroundUp = "ButtonNormalUp";
            enabled = true;
            icon = "";
            label = "";
            §§push("selected");
            §§push(false);
            if(false)
            {
               continue;
            }
            setProperty(§§pop(), _X, §§pop());
         }
         §§goto(addr0cb6);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(9));
      §§push(§§constant(6));
      break;
   }
   set(§§pop(),§§pop());
   set("\b\n\x05",false);
   addr0cb6:
}
