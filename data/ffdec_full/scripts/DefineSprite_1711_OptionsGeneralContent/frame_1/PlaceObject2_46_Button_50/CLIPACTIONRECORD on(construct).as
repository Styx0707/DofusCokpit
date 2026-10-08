on(construct){
   while(true)
   {
      if(!(0x2FA57DA1 & 0x2FA57DA1))
      {
         if(!(true or true))
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(ord(§§pop()))
      {
         if(!getTimer())
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         backgroundDown = "ButtonCheckDown";
         backgroundUp = "ButtonCheckUp";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr379b);
         }
      }
      set(§§pop(),§§pop());
      §§push(§§constant(9));
      §§push(§§constant(10));
      break;
   }
   set(§§pop(),§§pop());
   set("\b\t\b\n\x1d{invalid_utf8=150}\x04",true);
   addr379b:
}
