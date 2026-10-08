on(construct){
   while(true)
   {
      if(!ord("\n"))
      {
         if(false)
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
            §§push(getProperty(§§pop(), _X));
         }
         backgroundDown = "ButtonCraftDown";
         backgroundUp = "ButtonCraftUp";
         enabled = true;
         icon = "";
         §§push("label");
         §§push("");
         if(!(getTimer() + 1))
         {
            §§goto(addr67726);
         }
      }
      set(§§pop(),§§pop());
      §§push(§§constant(8));
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   set("\x1d{invalid_utf8=150}\x04","\b\b\x05");
   set("\x1d{invalid_utf8=150}\x04",false);
   addr67726:
   new §\§\§pop()§();
}
