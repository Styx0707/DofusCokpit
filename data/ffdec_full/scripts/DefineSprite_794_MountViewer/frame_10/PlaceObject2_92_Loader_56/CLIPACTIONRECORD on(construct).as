on(construct){
   loop1:
   while(true)
   {
      if(!ord("\x0b"))
      {
         if(!(0x2F1880AE & 0x2F1880AE))
         {
            break;
         }
      }
      else
      {
         §§push(379042009);
      }
      if(!(§§pop() - 1))
      {
         break;
      }
      addrf65e:
      while(true)
      {
         if(!(getTimer() + 1))
         {
            §§push(§§pop()(§§pop()));
            break;
         }
         autoLoad = true;
         centerContent = false;
         contentPath = "";
         enabled = false;
         §§push("fallbackContentPath");
         §§push("");
         if(getTimer() + 1)
         {
            break loop1;
         }
         var §§pop() = §§pop();
      }
      return;
   }
   set(§§pop(),§§pop());
   set("{invalid_utf8=155}{invalid_utf8=184}",false);
   set("\x1d{invalid_utf8=150}\x04",true);
   set("\b\x06\x05","\x1d{invalid_utf8=150}\x04");
   §§goto(addrf65e);
}
