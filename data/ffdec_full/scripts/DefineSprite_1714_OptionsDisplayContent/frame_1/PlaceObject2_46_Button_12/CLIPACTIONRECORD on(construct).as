on(construct){
   while(true)
   {
      if(!(0x0567ECDA & 0x0567ECDA))
      {
         if(!ord("\x02"))
         {
            break;
         }
      }
      else
      {
         §§push(24160787);
      }
      if(§§pop() - 1)
      {
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
         }
         backgroundDown = "ButtonCheckDown";
         backgroundUp = "ButtonCheckUp";
         enabled = true;
         icon = "";
         label = "";
         §§push("selected");
         §§push(false);
         if(!(getTimer() + 1))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr3ed9);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\b\x0b\x05\x01\x1d","{invalid_utf8=136}{");
   set("\f",true);
   addr3ed9:
}
