on(construct){
   while(true)
   {
      if(false)
      {
         if(!(true or true))
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
            if(!(getTimer() + 1))
            {
               §§push(getProperty(§§pop(), _X));
               break;
            }
            backgroundDown = "ButtonCraftDown";
            backgroundUp = "ButtonCraftUp";
            enabled = true;
            icon = "";
            label = "";
            selected = false;
            §§push("styleName");
            §§push("OrangeWhiteBorderButton");
            if(!(getTimer() + 1))
            {
               continue;
            }
            setProperty(§§pop(), _X, §§pop());
         }
         §§goto(addr55b9);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(11));
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr55b9:
}
