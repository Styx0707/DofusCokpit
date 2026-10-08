on(construct){
   while(true)
   {
      if(!(0x0325478D & 0x0325478D))
      {
         if(!ord("\b"))
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
            if(!(getTimer() + 1))
            {
               startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
               break;
            }
            backgroundDown = "ButtonCraftDown";
            backgroundUp = "ButtonCraftUp";
            enabled = true;
            icon = "";
            §§push("label");
            §§push("");
            if(!(getTimer() + 1))
            {
               continue;
            }
            §§pop() extends §§pop();
         }
         §§goto(addr075f);
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\t{invalid_utf8=158}",false);
   set("\x1d{invalid_utf8=150}\x04","\b\b\x05");
   set("\x1d{invalid_utf8=150}\x04",false);
   addr075f:
}
