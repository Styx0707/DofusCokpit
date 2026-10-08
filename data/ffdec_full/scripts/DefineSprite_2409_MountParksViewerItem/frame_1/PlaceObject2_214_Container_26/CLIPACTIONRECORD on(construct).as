on(construct){
   while(true)
   {
      if(!ord("\x05"))
      {
         if(!(true and true))
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
         if(!(getTimer() + 1))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         backgroundRenderer = "";
         set("\x16\x10\x12","");
         dragAndDrop = false;
         enabled = false;
         §§push("\x18\x07\x0e");
         §§push(false);
         if(!getTimer())
         {
            §§goto(addr16678);
         }
      }
      set(§§pop(),§§pop());
      set(§§constant(6),"{invalid_utf8=180}");
      break;
   }
   set("{invalid_utf8=180}",1);
   set("@",2);
   set("\x1d{invalid_utf8=150}\x04",false);
   set("\b\x06\b\x01\x1d{invalid_utf8=150}\x07","\b\x07\x07\x01");
   addr16678:
   getProperty(§§pop(), _X);
}
