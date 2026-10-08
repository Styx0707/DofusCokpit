on(construct){
   loop1:
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
         §§push("\x06");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      addr2ae4:
      while(true)
      {
         if(!ord("\x04"))
         {
            §§push(getProperty(§§pop(), _X));
            break;
         }
         autoLoad = true;
         centerContent = true;
         contentPath = "";
         enabled = false;
         fallbackContentPath = "";
         §§push("forceReload");
         §§push(false);
         break loop1;
         §§pop()[§§pop()] = §§pop();
      }
      return;
   }
   set(§§pop(),§§pop());
   set("{invalid_utf8=138}",true);
   w_ = "{invalid_utf8=153}m";
   §§goto(addr2ae4);
}
