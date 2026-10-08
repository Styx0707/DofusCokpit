on(construct){
   while(true)
   {
      if(!ord("\x02"))
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
         if(!getTimer())
         {
            §§push(getProperty(§§pop(), _X));
         }
         autoLoad = true;
         centerContent = false;
         contentPath = "";
         enabled = false;
         fallbackContentPath = "";
         §§push("forceReload");
         §§push(false);
         if(!(getTimer() + 1))
         {
            §§goto(addrc165);
         }
      }
      set(§§pop(),§§pop());
      §§push(§§constant(7));
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   set("\x19","C{invalid_utf8=131}");
   addrc165:
   getProperty(§§pop(), _X);
}
