on(construct){
   while(true)
   {
      if(!(0x1828DC26 | 0x1828DC26))
      {
         if(!ord("\b"))
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         if(!(getTimer() + 1))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         backgroundDown = "ButtonCraftDown";
         backgroundUp = "ButtonCraftUp";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(false)
         {
            §§goto(addr13642);
         }
      }
      set(§§pop(),§§pop());
      set(§§constant(9),§§constant(10));
      break;
   }
   set("\x1d",false);
   addr13642:
   §§pop()();
}
