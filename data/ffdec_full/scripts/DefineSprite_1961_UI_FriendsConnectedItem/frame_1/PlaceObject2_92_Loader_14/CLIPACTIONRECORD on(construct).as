on(construct){
   while(true)
   {
      if(!(0x277B787F & 0x277B787F))
      {
         if(!(true or true))
         {
            break;
         }
      }
      else
      {
         §§push("\x06");
      }
      if(ord(§§pop()))
      {
         if(!(getTimer() + 1))
         {
            §§push(getProperty(§§pop(), _X));
         }
         autoLoad = true;
         centerContent = false;
         contentPath = "";
         enabled = false;
         §§push("fallbackContentPath");
         §§push("");
         if(!getTimer())
         {
            §§goto(addrdb43);
         }
      }
      set(§§pop(),§§pop());
      set(§§constant(6),false);
      break;
   }
   set("{invalid_utf8=177}{invalid_utf8=202}",true);
   set("\x06\x16","S");
   addrdb43:
   new §\§\§pop()§();
}
