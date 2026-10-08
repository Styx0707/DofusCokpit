on(construct){
   while(true)
   {
      if(false)
      {
         if(!(0x04F3506F | 0x04F3506F))
         {
            break;
         }
      }
      else
      {
         §§push("\x05");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(!getTimer())
            {
               §§push(getProperty(§§pop(), _X));
               break;
            }
            autoLoad = true;
            centerContent = false;
            contentPath = "";
            enabled = false;
            §§push("fallbackContentPath");
            §§push("");
            if(false)
            {
               continue;
            }
            §§push(getProperty(§§pop(), _X));
         }
         §§goto(addr289af);
      }
      set(§§pop(),§§pop());
      set(§§constant(6),false);
      break;
   }
   set("{invalid_utf8=199}",true);
   set("]","\x1d{invalid_utf8=150}\x04");
   addr289af:
}
