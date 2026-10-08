on(construct){
   while(true)
   {
      if(false)
      {
         if(!(0x11229519 | 0x11229519))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         while(true)
         {
            if(!getTimer())
            {
               §§push(getProperty(§§pop(), _X));
               break;
            }
            backgroundDown = "ButtonValidDown";
            backgroundUp = "ButtonValidUp";
            enabled = true;
            icon = "";
            label = "";
            §§push("selected");
            §§push(false);
            if(!getTimer())
            {
               continue;
            }
            §§push(getProperty(§§pop(), _X));
         }
         §§goto(addr16002);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(9));
      §§push(§§constant(10));
      break;
   }
   set(§§pop(),§§pop());
   set("\x1d",false);
   addr16002:
}
