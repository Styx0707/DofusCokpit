on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\b"))
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
            if(!getTimer())
            {
               §§pop() extends §§pop();
               break;
            }
            backgroundDown = "ButtonNormalDown";
            backgroundUp = "ButtonNormalUp";
            enabled = true;
            icon = "";
            label = "";
            §§push("selected");
            §§push(false);
            if(!(getTimer() + 1))
            {
               continue;
            }
            setProperty(§§pop(), _X, §§pop());
         }
         §§goto(addr211b);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(9));
      §§push(§§constant(10));
      break;
   }
   set(§§pop(),§§pop());
   set("\b\x0b\x05",false);
   addr211b:
}
