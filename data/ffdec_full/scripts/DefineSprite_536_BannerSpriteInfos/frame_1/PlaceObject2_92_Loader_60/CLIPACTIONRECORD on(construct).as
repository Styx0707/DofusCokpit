on(construct){
   while(true)
   {
      if(!(0x0F95AB78 | 0x0F95AB78))
      {
         if(!ord("\x05"))
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(!ord("\t"))
            {
               setProperty(§§pop(), _X, §§pop());
               break;
            }
            autoLoad = true;
            centerContent = true;
            contentPath = "";
            enabled = false;
            fallbackContentPath = "";
            forceReload = false;
            §§push("scaleContent");
            §§push(true);
            if(!ord("\x04"))
            {
               continue;
            }
            §§pop()[§§pop()] = §§pop();
         }
         §§goto(addr17131);
      }
      set(§§pop(),§§pop());
      break;
   }
   h = "W\f";
   addr17131:
}
