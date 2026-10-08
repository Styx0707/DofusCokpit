on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\x02"))
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(!(getTimer() + 1))
            {
               startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
               break;
            }
            backgroundDown = "ButtonCheckDown";
            backgroundUp = "ButtonCheckUp";
            enabled = true;
            icon = "";
            label = "";
            selected = false;
            §§push("styleName");
            §§push("WhiteCheckButton");
            if(!getTimer())
            {
               continue;
            }
            setProperty(§§pop(), _X, §§pop());
         }
         §§goto(addrea0f);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(11));
      §§push(true);
      break;
   }
   set(§§pop(),§§pop());
   addrea0f:
}
