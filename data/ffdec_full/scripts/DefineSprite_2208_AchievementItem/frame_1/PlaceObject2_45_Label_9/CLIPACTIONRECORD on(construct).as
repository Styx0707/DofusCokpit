on(construct){
   while(true)
   {
      if(!(0x04B064A5 & 0x04B064A5))
      {
         if(!ord("\x06"))
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      enabled = true;
      html = false;
      multiline = false;
      styleName = "BrownCenterSmallLabel";
      text = "";
      §§push("wordWrap");
      §§push(true);
      if(false)
      {
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr15e2a);
      }
      break;
   }
   set(§§pop(),§§pop());
   addr15e2a:
}
