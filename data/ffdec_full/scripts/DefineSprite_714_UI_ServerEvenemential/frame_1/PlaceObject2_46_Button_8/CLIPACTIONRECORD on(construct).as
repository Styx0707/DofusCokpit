on(construct){
   while(true)
   {
      if(!ord("\n"))
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push("\n");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(false)
            {
               duplicateMovieClip(§§pop(),§§pop(),§§pop());
               break;
            }
            backgroundDown = "ButtonTabDown";
            backgroundUp = "ButtonTabUp";
            enabled = true;
            icon = "";
            label = "";
            §§push("selected");
            §§push(true);
            if(!getTimer())
            {
               continue;
            }
            §§push(getProperty(§§pop(), _X));
         }
         §§goto(addr8a49);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(9));
      §§push(§§constant(10));
      break;
   }
   set(§§pop(),§§pop());
   set("\b\x0b\x05\x01\x1d",true);
   addr8a49:
}
