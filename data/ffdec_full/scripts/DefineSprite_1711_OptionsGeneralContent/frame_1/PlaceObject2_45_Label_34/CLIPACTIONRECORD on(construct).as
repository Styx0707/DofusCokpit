on(construct){
   while(true)
   {
      if(!(0x16EDC541 & 0x16EDC541))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(!ord(§§pop()))
      {
         §§goto(addr17b50);
      }
      §§push("enabled");
      §§push(true);
      break;
   }
   set(§§pop(),§§pop());
   html = false;
   multiline = false;
   styleName = "BrownLeftSmallLabel";
   text = "";
   §§push("wordWrap");
   §§push(false);
   if(!getTimer())
   {
      §§push(getProperty(§§pop(), _X));
   }
   else
   {
      addr17b50:
      set(§§pop(),§§pop());
      §§goto(addr17bc8);
   }
   addr17bc8:
}
