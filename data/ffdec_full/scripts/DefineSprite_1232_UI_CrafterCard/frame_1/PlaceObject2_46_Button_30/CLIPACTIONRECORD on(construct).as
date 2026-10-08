on(construct){
   while(true)
   {
      if(!ord("\x06"))
      {
         if(!(0x32454486 & 0x32454486))
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
            if(!ord("\x02"))
            {
               §§pop() implements ;
               break;
            }
            backgroundDown = "ButtonCheckDown";
            backgroundUp = "ButtonCheckUp";
            enabled = false;
            icon = "";
            label = "";
            §§push("selected");
            §§push(false);
            if(!getTimer())
            {
               continue;
            }
            setProperty(§§pop(), _X, §§pop());
         }
         §§goto(addr15329);
      }
      set(§§pop(),§§pop());
      set(§§constant(9),§§constant(10));
      break;
   }
   set("{invalid_utf8=150}\x04",true);
   addr15329:
}
