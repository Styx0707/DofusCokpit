on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!ord("\x06"))
         {
            if(false)
            {
               §§goto(addr17522);
            }
         }
         else
         {
            §§push(false);
         }
         if(§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      §§goto(addr1760c);
   }
   addr1755c:
   if(false)
   {
      §§push(new §\§\§pop()§());
   }
   backgroundRenderer = "";
   set("\x16\x10\x12","");
   dragAndDrop = false;
   enabled = true;
   §§push("\x18\x07\x0e");
   §§push(false);
   if(getTimer())
   {
      set(§§pop(),§§pop());
      while(true)
      {
         set(":","\x05");
         set("\r",1);
         set("\x1d",3);
         set("\x1d{invalid_utf8=150}\x04",true);
         §§push("\b\x06\b\x01\x1d{invalid_utf8=150}\x07");
         §§push("\b\x07\x07\x01");
         if(ord("\x04"))
         {
            break loop2;
         }
         var §§pop() = §§pop();
         §§goto(addr1755c);
         set(§§pop(),§§pop());
      }
      break loop2;
      addr17522:
   }
   §§pop()[§§pop()] = §§pop();
   addr1760c:
}
