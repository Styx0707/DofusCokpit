on(construct){
   while(true)
   {
      if(!(0x38E126EE & 0x38E126EE))
      {
         if(!ord("\n"))
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
            if(!getTimer())
            {
               §§push(getProperty(§§pop(), _X));
               break;
            }
            backgroundRenderer = "";
            set("\x16\x10\x12","");
            dragAndDrop = false;
            enabled = true;
            §§push("\x18\x07\x0e");
            §§push(true);
            if(!(getTimer() + 1))
            {
               continue;
            }
            §§push(new §\§\§pop()§());
         }
         §§goto(addr3b51);
      }
      set(§§pop(),§§pop());
      break;
   }
   set("%V","\x1d{invalid_utf8=150}\x04");
   set("\b\x06\b\x07\x1d{invalid_utf8=150}\x07",1);
   set("\b\b\x07\x01",2);
   set("",false);
   set("","\x1d{invalid_utf8=150}\x07");
   addr3b51:
}
